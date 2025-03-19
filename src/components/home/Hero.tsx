import React from 'react';
import { Rocket, Code, Users, Star, Award, BookOpen } from 'lucide-react';

export function Hero() {
  return (
    <div className="relative bg-white">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto">
          <div className="relative z-10 pb-8 bg-white sm:pb-16 md:pb-20 lg:w-full lg:pb-28 xl:pb-32">
            <main className="mt-10 mx-auto max-w-7xl px-4 sm:mt-12 sm:px-6 md:mt-16 lg:mt-20 lg:px-8 xl:mt-28">
              <div className="sm:text-center lg:text-left">
                <h1 className="text-4xl tracking-tight font-extrabold text-gray-900 sm:text-5xl md:text-6xl">
                  <span className="block">Master Tech Skills</span>
                  <span className="block text-indigo-600">Advance Your Career</span>
                </h1>
                <p className="mt-3 text-base text-gray-500 sm:mt-5 sm:text-lg sm:max-w-xl sm:mx-auto md:mt-5 md:text-xl lg:mx-0">
                  Join 50,000+ developers learning from industry experts through structured paths, hands-on projects, and a supportive community.
                </p>
                <div className="mt-5 sm:mt-8 sm:flex sm:justify-center lg:justify-start">
                  <div className="rounded-md shadow">
                    <a
                      href="/sign-up"
                      className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 md:py-4 md:text-lg md:px-10"
                    >
                      Start Learning Free
                    </a>
                  </div>
                  <div className="mt-3 sm:mt-0 sm:ml-3">
                    <a
                      href="/learn"
                      className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200 md:py-4 md:text-lg md:px-10"
                    >
                      Browse Courses
                    </a>
                  </div>
                </div>
              </div>
            </main>
          </div>
        </div>
        <div className="lg:absolute lg:inset-y-0 lg:right-0 lg:w-1/2">
          <img
            className="h-56 w-full object-cover sm:h-72 md:h-96 lg:w-full lg:h-full"
            src="https://images.unsplash.com/photo-1522071820081-009f0129c71c?ixlib=rb-1.2.1&auto=format&fit=crop&w=2850&q=80"
            alt="Tech professionals collaborating"
          />
        </div>
      </div>

      {/* Social Proof Section */}
      <div className="bg-gray-50 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
            <div className="flex flex-col items-center">
              <span className="text-3xl font-bold text-indigo-600">50K+</span>
              <span className="mt-2 text-sm text-gray-500">Active Learners</span>
            </div>
            <div className="flex flex-col items-center">
              <span className="text-3xl font-bold text-indigo-600">200+</span>
              <span className="mt-2 text-sm text-gray-500">Video Courses</span>
            </div>
            <div className="flex flex-col items-center">
              <span className="text-3xl font-bold text-indigo-600">95%</span>
              <span className="mt-2 text-sm text-gray-500">Success Rate</span>
            </div>
            <div className="flex flex-col items-center">
              <span className="text-3xl font-bold text-indigo-600">4.8/5</span>
              <span className="mt-2 text-sm text-gray-500">Student Rating</span>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-extrabold text-gray-900">Why Choose TechPath?</h2>
            <p className="mt-4 text-lg text-gray-500">Everything you need to accelerate your tech career</p>
          </div>

          <div className="mt-12 grid gap-8 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-100">
              <div className="flex items-center">
                <BookOpen className="h-6 w-6 text-indigo-600" />
                <h3 className="ml-3 text-lg font-medium text-gray-900">Structured Learning Paths</h3>
              </div>
              <p className="mt-4 text-gray-500">
                Curated courses designed by industry experts to take you from beginner to professional.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-100">
              <div className="flex items-center">
                <Code className="h-6 w-6 text-indigo-600" />
                <h3 className="ml-3 text-lg font-medium text-gray-900">Hands-on Projects</h3>
              </div>
              <p className="mt-4 text-gray-500">
                Build real-world applications with guidance from experienced developers.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-100">
              <div className="flex items-center">
                <Users className="h-6 w-6 text-indigo-600" />
                <h3 className="ml-3 text-lg font-medium text-gray-900">Community Support</h3>
              </div>
              <p className="mt-4 text-gray-500">
                Connect with peers, mentors, and industry experts in our active community.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Testimonials Section */}
      <div className="bg-gray-50 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-extrabold text-center text-gray-900 mb-12">
            What Our Students Say
          </h2>
          <div className="grid gap-8 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="flex items-center mb-4">
                <div className="flex text-yellow-400">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="h-5 w-5 fill-current" />
                  ))}
                </div>
              </div>
              <p className="text-gray-600 mb-4">
                "TechPath helped me transition from a junior to senior developer in just 8 months. The structured learning paths and community support made all the difference."
              </p>
              <div className="flex items-center">
                <img
                  className="h-10 w-10 rounded-full"
                  src="https://images.unsplash.com/photo-1494790108377-be9c29b29330?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80"
                  alt="Sarah Chen"
                />
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-900">Sarah Chen</p>
                  <p className="text-sm text-gray-500">Senior Developer at Tech Co</p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="flex items-center mb-4">
                <div className="flex text-yellow-400">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="h-5 w-5 fill-current" />
                  ))}
                </div>
              </div>
              <p className="text-gray-600 mb-4">
                "The project-based learning approach gave me practical experience that I could immediately apply to my job. Worth every minute invested."
              </p>
              <div className="flex items-center">
                <img
                  className="h-10 w-10 rounded-full"
                  src="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80"
                  alt="Michael Torres"
                />
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-900">Michael Torres</p>
                  <p className="text-sm text-gray-500">Full Stack Developer</p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="flex items-center mb-4">
                <div className="flex text-yellow-400">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="h-5 w-5 fill-current" />
                  ))}
                </div>
              </div>
              <p className="text-gray-600 mb-4">
                "The community support is incredible. Having access to mentors and other learners made the journey so much easier and more enjoyable."
              </p>
              <div className="flex items-center">
                <img
                  className="h-10 w-10 rounded-full"
                  src="https://images.unsplash.com/photo-1438761681033-6461ffad8d80?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80"
                  alt="Emily Johnson"
                />
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-900">Emily Johnson</p>
                  <p className="text-sm text-gray-500">Frontend Developer</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-indigo-700">
        <div className="max-w-2xl mx-auto text-center py-16 px-4 sm:py-20 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-extrabold text-white sm:text-4xl">
            <span className="block">Ready to Start Your Journey?</span>
          </h2>
          <p className="mt-4 text-lg leading-6 text-indigo-200">
            Join thousands of developers who are already advancing their careers with TechPath.
          </p>
          <a
            href="/sign-up"
            className="mt-8 w-full inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-indigo-600 bg-white hover:bg-indigo-50 sm:w-auto"
          >
            Get Started Free
          </a>
        </div>
      </div>
    </div>
  );
}